package com.example.outlookclone.model

import kotlinx.serialization.Serializable

@Serializable
data class Message(
    val id: String,
    val sender: String,
    val subject: String,
    val preview: String,
    val body: String,
    val timestampEpochMs: Long
)
