from marshmallow import INCLUDE, Schema, fields, post_dump, post_load, validate

from binit.core.constants import ARCH_ALIASES, SUPPORTED_PLATFORMS
from binit.models import ConfigModel, ToolModel


class ToolSchema(Schema):
    name = fields.Str(required=True)
    repo = fields.Url(required=True)
    asset = fields.Str(required=True)
    release = fields.Str(required=True)
    version = fields.Str(required=True, validate=validate.Regexp(r'^\d+(\.\d+)+$', error='Version must be numeric (e.g. 1.2.3)'))
    homepage = fields.Url(allow_none=True)
    updated_at = fields.DateTime(required=True)
    installed_at = fields.DateTime(allow_none=True)
    description = fields.Str(allow_none=True)
    license = fields.Str(allow_none=True)
    binary = fields.Str(required=True)
    rename_to = fields.Str(load_default=None, allow_none=True)


    class Meta:
        unknown = INCLUDE


    @post_dump
    def drop_none_rename(self, data, **kwargs):
        if data.get('rename_to') is None:
            data.pop('rename_to', None)
        return data

    @post_load
    def make(self, data, **kwargs):
        return ToolModel(**data)


class ConfigSchema(Schema):
    binit_version = fields.Str(required=True)
    os = fields.Str(required=True, validate=validate.OneOf(SUPPORTED_PLATFORMS))
    arch = fields.Str(required=True, validate=validate.OneOf(ARCH_ALIASES.keys()))
    init_at = fields.DateTime(required=True)
    installed_tools = fields.Dict(keys=fields.Str(), values=fields.Nested(ToolSchema), required=True)


    class Meta:
        unknown = INCLUDE


    @post_load
    def make(self, data, **kwargs):
        return ConfigModel(**data)
