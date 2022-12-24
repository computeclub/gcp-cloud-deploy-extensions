# -*- coding: utf-8 -*-
"""
types defines the pydantic types of the relevant pubsub messages
"""
from pydantic import BaseModel


class BaseAttributes(BaseModel):
    """BaseAttributes."""

    Action: str
    DeliveryPipelineId: str
    Location: str
    ProjectNumber: str
    ReleaseId: str


class ResourcesAttributes(BaseAttributes):
    """ResourcesAttributes."""

    Resource: str
    ResourceType: str


class ApprovalsAttributes(BaseAttributes):
    """ApprovalsAttributes."""

    Rollout: str
    RolloutId: str
    TargetId: str


class OperationsAttributes(BaseAttributes):
    """OperationsAttributes."""

    JobId: str
    JobRunId: str
    JobType: str
    PhaseId: str
    Resource: str
    ResourceType: str
    RolloutId: str
    TargetId: str


class Message(BaseModel):
    """Message."""

    attributes: ApprovalsAttributes | OperationsAttributes | ResourcesAttributes
    messageId: str
    message_id: str
    publishTime: str
    publish_time: str


class PubSubEnvelope(BaseModel):
    """PubSubEnvelope."""

    message: Message
    subscription: str
