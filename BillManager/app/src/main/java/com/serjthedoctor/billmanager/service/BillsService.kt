package com.serjthedoctor.billmanager.service

import com.serjthedoctor.billmanager.domain.Bill
import com.serjthedoctor.billmanager.domain.Dto
import okhttp3.MultipartBody
import retrofit2.http.*

interface BillsService {
    companion object {
        const val API = "https://db28f9f0f7e3.ngrok.io"
        const val FLASK_API = "http://192.168.0.127:5000"
    }

    @GET("/bills")
    suspend fun getAll(): List<Bill>

    @POST("/bills")
    suspend fun addOne(@Body bill: Bill): Bill

    @PUT("/bills/{id}")
    suspend fun updateOne(@Path("id") id: Int, @Body bill: Bill): Bill

    @DELETE("/bills/{id}")
    suspend fun deleteOne(@Path("id") id: Int): Bill

    @Multipart
    @POST("/receipts")
    suspend fun uploadReceipt(@Part image: MultipartBody.Part): Dto
}