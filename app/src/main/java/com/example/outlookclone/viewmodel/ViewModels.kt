package com.example.outlookclone.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.outlookclone.model.Message
import com.example.outlookclone.repo.MailRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class InboxViewModel : ViewModel() {
    private val repository = MailRepository()
    private val _uiState = MutableStateFlow(InboxState())
    val uiState: StateFlow<InboxState> = _uiState

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            runCatching { repository.fetchInbox() }
                .onSuccess { msgs -> _uiState.value = InboxState(messages = msgs, isLoading = false) }
                .onFailure { _ -> _uiState.value = InboxState(messages = emptyList(), isLoading = false) }
        }
    }
}

data class InboxState(
    val messages: List<Message> = emptyList(),
    val isLoading: Boolean = false
)

class EmailDetailViewModel : ViewModel() {
    private val repository = MailRepository()
    private val _state = MutableStateFlow<Message?>(null)
    val state: StateFlow<Message?> = _state

    fun load(id: String) {
        viewModelScope.launch {
            runCatching { repository.fetchMessage(id) }
                .onSuccess { _state.value = it }
        }
    }
}
