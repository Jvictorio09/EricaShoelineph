import os

class CloudinaryImageMixin:
    def get_image_url(self):
        if hasattr(self, 'image') and self.image:
            url = self.image.url

            # Try to extract extension from MIME type
            try:
                content_type = self.image.file.content_type
                ext = {
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/webp': '.webp',
                }.get(content_type, '')

                if url.startswith("https://res.cloudinary.com") and not url.endswith(ext):
                    return url + ext
            except Exception as e:
                print("⚠️ Error getting extension from content_type:", e)

            return url

        return "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1742581072/logo_y0qp26.png"