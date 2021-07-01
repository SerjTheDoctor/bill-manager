package com.serjthedoctor.billmanager.lib

import android.text.Editable
import android.text.TextWatcher
import android.util.Log
import android.view.KeyEvent
import android.view.View
import android.widget.EditText
import android.widget.TextView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleObserver
import androidx.lifecycle.OnLifecycleEvent
import kotlinx.coroutines.*

class DebouncingSearchTextListener(
    lifecycle: Lifecycle,
    private val debounceTime: Long = 1000,
    private val onTextChange: (String?) -> Unit
): TextWatcher, LifecycleObserver {
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.Main)
    private var searchJob: Job? = null

    init {
        lifecycle.addObserver(this)
    }

    override fun beforeTextChanged(p0: CharSequence?, p1: Int, p2: Int, p3: Int) {}

    override fun onTextChanged(p0: CharSequence?, p1: Int, p2: Int, p3: Int) {}

    override fun afterTextChanged(p0: Editable?) {
        Log.d("[Debouncing]", "onKey()")
        searchJob?.cancel()
        searchJob = scope.launch {
            val text = p0?.toString()
            Log.d("[Debouncing]", "launching with text: $text")
            text.let {
                delay(debounceTime)
                onTextChange(text)
            }
        }
    }

    @OnLifecycleEvent(Lifecycle.Event.ON_DESTROY)
    private fun destroy() {
        searchJob?.cancel()
    }
}