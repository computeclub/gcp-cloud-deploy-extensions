# -*- coding: utf-8 -*-
"""
types defines the pydantic types of the relevant pubsub messages
"""
from typing import Literal, Optional

from pydantic import BaseModel


class BaseAttributes(BaseModel):
    """BaseAttributes."""

    DeliveryPipelineId: Optional[str]
    Location: str
    ProjectNumber: str
    ReleaseId: Optional[str]
    RolloutId: Optional[str]
    TargetId: Optional[str]


class ResourcesAttributes(BaseAttributes):
    """ResourcesAttributes."""

    Action: Literal[
        "Create",
        "Update",
    ]
    JobRunId: Optional[str]
    Resource: str
    ResourceType: str


class ApprovalsAttributes(BaseAttributes):
    """ApprovalsAttributes."""

    Action: str
    Rollout: str


class OperationsAttributes(BaseAttributes):
    """OperationsAttributes."""

    Action: Literal[
        "Start",
        "Succeed",
        "Failure",
    ]
    JobId: Optional[str]
    JobRunId: Optional[str]
    JobType: Optional[str]
    PhaseId: Optional[str]
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
