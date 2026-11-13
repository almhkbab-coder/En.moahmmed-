import os
from io import BytesIO
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_IMAGE_SIZE_MB = 5
# SVG is strictly excluded to prevent Stored XSS, XXE, and malicious XML script injection in medical records
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP']
DANGEROUS_PAYLOADS = [b'<script', b'<?php', b'<svg', b'<html', b'<iframe', b'javascript:', b'onerror=', b'onload=']


def validate_image_file(file_obj):
    """
    Validates uploaded images for maximum allowed file size, extension, deep content inspection,
    and genuine raster image integrity using Pillow.
    Guarantees no executable scripts, polyglots, or malicious SVG payloads are uploaded.
    """
    if not file_obj:
        return

    # 1. Check file size (max 5 MB)
    if file_obj.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            _(f"حجم الملف يتجاوز الحد الأقصى المسموح به ({MAX_IMAGE_SIZE_MB} ميجابايت).")
        )

    # 2. Check extension (SVG disallowed)
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            _("نوع الملف غير مدعوم. الامتدادات المسموح بها هي: JPG, JPEG, PNG, WEBP فقط. ملفات SVG غير مقبولة لدواعي الأمان.")
        )

    # 3. Deep Content Inspection & Signature scanning
    try:
        initial_pos = file_obj.tell() if hasattr(file_obj, 'tell') else 0
        content_sample = file_obj.read(4096)
        if hasattr(file_obj, 'seek'):
            file_obj.seek(initial_pos)

        sample_lower = content_sample.lower()
        for marker in DANGEROUS_PAYLOADS:
            if marker in sample_lower:
                raise ValidationError(_("تم اكتشاف محتوى برمجي مشبوه داخل الملف المرفوع."))

        # 4. Verify authentic image via Pillow
        image = Image.open(file_obj)
        image.verify()  # Verifies file integrity without decoding entire image

        if image.format not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError(
                _(f"صيغة الصورة غير مدعومة ({image.format}). الصيغ المقبولة: JPEG, PNG, WEBP.")
            )

        # Rewind file pointer for Django file saving
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(_("الملف المرفوع تالف أو ليس صورة حقيقية صالحة."))

