from typing import List

from rallp_config.common.types.list import ListConfig
from rallp_config.common.utils.dictionary import merge_dict
from rallp_config.platform.types.attachment import BaseAttachment


class AttachmentListConfig(ListConfig[BaseAttachment, str]):

    def __init__(self) -> None:
        super().__init__(
            uid=lambda obj: obj.get_name(),
            obj_type=BaseAttachment,
            uid_type=str
        )

    def to_dict(self) -> dict:
        d = {}
        for decoration in self.get_all():
            merge_dict(d, decoration.to_dict())
        return d


# Attachments Config
# - to be used by all platforms.
class AttachmentsConfig:

    def __init__(
            self,
            attachment,
            config: dict = {}
            ) -> None:
        self._attach_type = attachment
        self._attachments = AttachmentListConfig()
        self.config = config

    def __add__(self, other):
        self._attachments.extend(other.get_all())
        return self

    def get_all(self) -> List[BaseAttachment]:
        return self._attachments.get_all()

    @property
    def config(self):
        return [a.to_dict() for a in self.get_all()]

    @config.setter
    def config(self, attachments: list):
        # Clear Previous
        self._attachments.remove_all()
        # Load New
        for a in attachments:
            if self._attach_type.is_valid(a['type']):
                attachment = self._attach_type(a['type'])()
                attachment.from_dict(a)
                self._attachments.add(attachment)
