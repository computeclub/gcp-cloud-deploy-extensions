# -*- coding: utf-8 -*-
"""
types defines the pydantic types of the relevant pubsub messages
"""
from typing import Optional

from pydantic import BaseModel


class BaseAttributes(BaseModel):
    """BaseAttributes."""

    Action: str
    DeliveryPipelineId: Optional[str]
    Location: str
    ProjectNumber: str
    ReleaseId: Optional[str]
    TargetId: Optional[str]
    RolloutId: Optional[str]


class ResourcesAttributes(BaseAttributes):
    """ResourcesAttributes."""

    Resource: str
    ResourceType: str


class ApprovalsAttributes(BaseAttributes):
    """ApprovalsAttributes."""

    Rollout: str


class OperationsAttributes(BaseAttributes):
    """OperationsAttributes."""

    JobId: str
    JobRunId: str
    JobType: str
    PhaseId: str
    Resource: str
    ResourceType: str


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
