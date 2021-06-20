package com.serjthedoctor.billmanager.service

import android.annotation.SuppressLint
import com.google.gson.*
import com.google.gson.stream.JsonReader
import com.google.gson.stream.JsonWriter
import com.serjthedoctor.billmanager.domain.BillStatus
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.lang.reflect.Type
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.*


object ServiceFactory {
    private val interceptor: HttpLoggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BASIC
    }

    private val client: OkHttpClient = OkHttpClient().newBuilder().apply {
        addInterceptor(interceptor)
    }.build()

    @SuppressLint("NewApi")
    private val gson: Gson = GsonBuilder()
        .setLenient()
        .registerTypeAdapter(BillStatus::class.java, object : TypeAdapter<BillStatus>() {
            override fun write(out: JsonWriter?, value: BillStatus?) {
                out?.value(value?.name)
            }

            override fun read(inn: JsonReader?): BillStatus {
                return inn?.nextString()
                    ?.let { BillStatus.valueOf(it.toUpperCase(Locale.ROOT)) }
                    ?: BillStatus.QUEUED
            }
        })
        .registerTypeAdapter(LocalDate::class.java, object : TypeAdapter<LocalDate>() {
            override fun write(out: JsonWriter?, value: LocalDate?) {
                out?.value(value?.format(DateTimeFormatter.ofPattern("yyyy-MM-dd")))
            }

            override fun read(readIn: JsonReader?): LocalDate? {
                return try {
                    LocalDate.parse(readIn?.nextString())
                } catch (e: IllegalStateException) {
                    readIn?.nextNull()
                    null
                }
            }
        })
        .create()

    fun <T> createService(cls: Class<T>, api: String): T = Retrofit.Builder()
        .addConverterFactory(GsonConverterFactory.create(gson))
        .baseUrl(api)
        .client(client)
        .build()
        .create(cls)
}