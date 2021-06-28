package com.serjthedoctor.billmanager.service

import com.serjthedoctor.billmanager.domain.Item
import com.serjthedoctor.billmanager.domain.Product
import retrofit2.Call
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Path
import retrofit2.http.Query

interface ProductsService {
    companion object {
        const val FLASK_API = "http://192.168.0.127:5000"
        const val RAILS_API = "http://192.168.0.127:3000"
    }

    @GET("/products")
    fun getByName(
        @Header("Authorization") token: String,
        @Query("name") name: String
    ): Call<List<Product>>
}