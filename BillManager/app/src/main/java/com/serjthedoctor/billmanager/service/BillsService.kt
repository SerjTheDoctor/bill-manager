package com.serjthedoctor.billmanager.service

import com.serjthedoctor.billmanager.domain.Bill
import com.serjthedoctor.billmanager.domain.Dto
import okhttp3.MultipartBody
import retrofit2.Call
import retrofit2.http.*

interface BillsService {
    companion object {
        const val FLASK_API = "http://192.168.0.127:5000"
        const val RAILS_API = "http://192.168.0.127:3000"
    }

    @GET("/bills")
    fun getAll(@Header("Authorization") token: String): Call<List<Bill>>

    @GET("/bills/{id}")
    fun getOne(
        @Header("Authorization") token: String,
        @Path("id") id: Int
    ): Call<Bill>

    @Multipart
    @POST("/bills")
    fun uploadReceipt(
        @Header("Authorization") token: String,
        @Part image: MultipartBody.Part
    ): Call<Bill>

    @PUT("/bills/{id}")
    fun updateOne(
        @Header("Authorization") token: String,
        @Path("id") id: Int,
        @Body bill: Bill
    ): Call<Bill>

    @DELETE("/bills/{id}")
    fun deleteOne(
        @Header("Authorization") token: String,
        @Path("id") id: Int
    ): Call<Bill>
}