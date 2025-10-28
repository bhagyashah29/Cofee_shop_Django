package com.example.shared.model

import kotlinx.serialization.Serializable

@Serializable
data class EmailFolder(
    val id: String,
    val name: String,
)

@Serializable
data class EmailMessage(
    val id: String,
    val folderId: String,
    val subject: String,
    val preview: String,
    val body: String,
)

@Serializable
data class NewMessageRequest(
    val to: String,
    val subject: String,
    val body: String,
)
