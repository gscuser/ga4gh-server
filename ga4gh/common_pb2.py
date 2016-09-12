# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ga4gh/common.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='ga4gh/common.proto',
  package='ga4gh',
  syntax='proto3',
  serialized_pb=_b('\n\x12ga4gh/common.proto\x12\x05ga4gh\"2\n\x0bGAException\x12\x12\n\nerror_code\x18\x01 \x01(\x05\x12\x0f\n\x07message\x18\x02 \x01(\t\"S\n\x08Position\x12\x16\n\x0ereference_name\x18\x01 \x01(\t\x12\x10\n\x08position\x18\x02 \x01(\x03\x12\x1d\n\x06strand\x18\x03 \x01(\x0e\x32\r.ga4gh.Strand\"K\n\x12\x45xternalIdentifier\x12\x10\n\x08\x64\x61tabase\x18\x01 \x01(\t\x12\x12\n\nidentifier\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t*@\n\x06Strand\x12\x16\n\x12STRAND_UNSPECIFIED\x10\x00\x12\x0e\n\nNEG_STRAND\x10\x01\x12\x0e\n\nPOS_STRAND\x10\x02\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_STRAND = _descriptor.EnumDescriptor(
  name='Strand',
  full_name='ga4gh.Strand',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STRAND_UNSPECIFIED', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NEG_STRAND', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='POS_STRAND', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=243,
  serialized_end=307,
)
_sym_db.RegisterEnumDescriptor(_STRAND)

Strand = enum_type_wrapper.EnumTypeWrapper(_STRAND)
STRAND_UNSPECIFIED = 0
NEG_STRAND = 1
POS_STRAND = 2



_GAEXCEPTION = _descriptor.Descriptor(
  name='GAException',
  full_name='ga4gh.GAException',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='error_code', full_name='ga4gh.GAException.error_code', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='message', full_name='ga4gh.GAException.message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=29,
  serialized_end=79,
)


_POSITION = _descriptor.Descriptor(
  name='Position',
  full_name='ga4gh.Position',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='reference_name', full_name='ga4gh.Position.reference_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='position', full_name='ga4gh.Position.position', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='strand', full_name='ga4gh.Position.strand', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=81,
  serialized_end=164,
)


_EXTERNALIDENTIFIER = _descriptor.Descriptor(
  name='ExternalIdentifier',
  full_name='ga4gh.ExternalIdentifier',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='database', full_name='ga4gh.ExternalIdentifier.database', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='identifier', full_name='ga4gh.ExternalIdentifier.identifier', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='version', full_name='ga4gh.ExternalIdentifier.version', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=166,
  serialized_end=241,
)

_POSITION.fields_by_name['strand'].enum_type = _STRAND
DESCRIPTOR.message_types_by_name['GAException'] = _GAEXCEPTION
DESCRIPTOR.message_types_by_name['Position'] = _POSITION
DESCRIPTOR.message_types_by_name['ExternalIdentifier'] = _EXTERNALIDENTIFIER
DESCRIPTOR.enum_types_by_name['Strand'] = _STRAND

GAException = _reflection.GeneratedProtocolMessageType('GAException', (_message.Message,), dict(
  DESCRIPTOR = _GAEXCEPTION,
  __module__ = 'ga4gh.common_pb2'
  # @@protoc_insertion_point(class_scope:ga4gh.GAException)
  ))
_sym_db.RegisterMessage(GAException)

Position = _reflection.GeneratedProtocolMessageType('Position', (_message.Message,), dict(
  DESCRIPTOR = _POSITION,
  __module__ = 'ga4gh.common_pb2'
  # @@protoc_insertion_point(class_scope:ga4gh.Position)
  ))
_sym_db.RegisterMessage(Position)

ExternalIdentifier = _reflection.GeneratedProtocolMessageType('ExternalIdentifier', (_message.Message,), dict(
  DESCRIPTOR = _EXTERNALIDENTIFIER,
  __module__ = 'ga4gh.common_pb2'
  # @@protoc_insertion_point(class_scope:ga4gh.ExternalIdentifier)
  ))
_sym_db.RegisterMessage(ExternalIdentifier)


# @@protoc_insertion_point(module_scope)
