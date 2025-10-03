package com.example.outlookclone.repo

import com.example.outlookclone.model.Message
import com.example.outlookclone.network.ApiClient
import com.example.outlookclone.network.SendMessageRequest

class MailRepository {
    suspend fun fetchInbox(): List<Message> = ApiClient.service.listMessages().map {
        Message(
            id = it.id,
            sender = it.sender,
            subject = it.subject,
            preview = it.preview,
            body = it.body,
            timestampEpochMs = it.timestampEpochMs
        )
    }

    suspend fun fetchMessage(id: String): Message = ApiClient.service.getMessage(id).let {
        Message(
            id = it.id,
            sender = it.sender,
            subject = it.subject,
            preview = it.preview,
            body = it.body,
            timestampEpochMs = it.timestampEpochMs
        )
    }

    suspend fun sendMessage(to: String, subject: String, body: String): String {
        val resp = ApiClient.service.sendMessage(SendMessageRequest(to, subject, body))
        return resp.id
    }
}
