package com.serjthedoctor.billmanager.service

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ServiceFactory {
    private val interceptor: HttpLoggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BASIC
    }

    private val client: OkHttpClient = OkHttpClient().newBuilder().apply {
        addInterceptor(interceptor)
    }.build()

    private val gson: Gson = GsonBuilder().setLenient().create()

    fun <T> createService(cls: Class<T>, api: String): T = Retrofit.Builder()
        .addConverterFactory(GsonConverterFactory.create(gson))
        .baseUrl(api)
        .client(client)
        .build()
        .create(cls)
}