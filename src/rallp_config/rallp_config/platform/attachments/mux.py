from rallp_config.common.types.platform import Platform
from rallp_config.platform.attachments.rallp import RallpAttachment
from rallp_config.platform.attachments.config import AttachmentsConfig
from rallp_config.platform.attachments.generic import GENERICAttachment
from rallp_config.platform.types.attachment import BaseAttachment


class AttachmentsConfigMux:
    PLATFORM = {
        Platform.Rallp: AttachmentsConfig(RallpAttachment),
        Platform.GENERIC: AttachmentsConfig(GENERICAttachment)
    }

    def __new__(cls, platform: str, attachments: dict = None) -> AttachmentsConfig:
        # Check Platform is Supported
        assert platform in cls.PLATFORM, f'Platform "{platform}" must be one of "{cls.PLATFORM.keys()}"'  # noqa:E501
        if not attachments:
            return cls.PLATFORM[platform]
        # Pre-Process Entries
        attachments = AttachmentsConfigMux.preprocess(platform, attachments)
        # Add All Attachments
        attachments_config = AttachmentsConfig(BaseAttachment)
        for p in cls.PLATFORM:
            cls.PLATFORM[p].config = attachments
            attachments_config += cls.PLATFORM[p]
        return attachments_config

    @staticmethod
    def preprocess(platform: str, attachments: dict):
        for i, a in enumerate(attachments):
            assert 'name' in a, 'An attachment is missing "name"'
            assert 'type' in a, 'An attachment is missing "type"'
            if '.' not in a['type']:
                a['type'] = '%s.%s' % (platform, a['type'])
            attachments[i] = a
        return attachments
