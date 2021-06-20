package com.serjthedoctor.billmanager.service

import android.app.Application
import android.content.Intent
import com.serjthedoctor.billmanager.LoginActivity
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

abstract class CustomCallback<T>(private val context: Application): Callback<T> {
    override fun onResponse(call: Call<T>, response: Response<T>) {
        if (response.code() == 401) {
            val intent = Intent(context, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            context.startActivity(intent)
        } else {
            onSuccess(call, response)
        }
    }

    abstract fun onSuccess(call: Call<T>, response: Response<T>)
}