import os
import tempfile

from django.conf import settings

from allauth_api.settings import allauth_api_settings

try:
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


if HAS_PIL:
    class BaseImageKeyGenerator(object):
        """
        Base class for image key generators
        """
        image_format = "PNG"

        def create_image_key(self, key):
            self.key = key
            image = self.create_image()
            image = self.resize_image(image)
            image = self.inscribe_image(image)
            return self.export_image(image)

        def get_image_format(self):
            return getattr(allauth_api_settings, "IMAGE_KEY_FORMAT", self.image_format)

        def get_image_size(self):
            return getattr(allauth_api_settings, "IMAGE_KEY_SIZE", None)

        def get_image_options(self):
            return {}

        def resize_image(self, image):
            current_size = image.size
            final_size = self.get_image_size()
            if final_size is not None and final_size != current_size:
                return image.thumbnail(final_size)
            return image

        def create_image(self):
            raise NotImplementedError("subclass and implement")

        def inscribe_image(self, image):
            return image

        def export_image(self, image):
            options = self.get_image_options()
            outfile = tempfile.NamedTemporaryFile()
            image.save(outfile, format=self.get_image_format(), **options)
            outfile.seek(0)
            return outfile

    class TemplateImageMixin(object):
        image_template = os.path.join(settings.STATIC_ROOT, 'allauth_api', 'key.png')

        def create_image(self):
            """
            Just loads a template image
            """
            template = self.get_template_image()
            image = Image.open(template)
            return image

        def get_template_image(self):
            return getattr(allauth_api_settings, "IMAGE_KEY_TEMPLATE", self.image_template)

    class TextImageMixin(object):
        """
        Creates an image using the key
        """
        # TODO
        pass

    class MetadataInscriptionMixin(object):
        """
        Adds the key to embedded image metadata.  Currently only png and jpg files are supported
        """
        def get_image_options(self):
            options = {}
            image_format = self.get_image_format()

            if image_format == 'PNG':
                info = PngInfo()
                info.add_text('key', self.key)
                options['pnginfo'] = info
            # elif image_format = 'JPEG':  # TODO
            #     options['exif'] =

            return options

    class SuperimposeInscriptionMixin(object):
        """
        Superimposes the key onto the image
        """
        # TODO

    class Base64ExporterMixin(object):
        pass

    class PNGImageKeyGenerator(TemplateImageMixin, MetadataInscriptionMixin, BaseImageKeyGenerator):
        pass
