package com.serjthedoctor.billmanager.model

import android.app.Application
import android.content.Intent
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import com.serjthedoctor.billmanager.LoginActivity
import com.serjthedoctor.billmanager.domain.Item
import com.serjthedoctor.billmanager.domain.Product
import com.serjthedoctor.billmanager.service.CustomCallback
import com.serjthedoctor.billmanager.service.ProductsService
import com.serjthedoctor.billmanager.service.ServiceFactory
import com.serjthedoctor.billmanager.service.SessionManager
import retrofit2.Call
import retrofit2.Response

class ProductsModel(application: Application) : AndroidViewModel(application) {
    private val app: Application = application
    private val sessionManager: SessionManager = SessionManager(application)
    private val service: ProductsService = ServiceFactory.createService(
        ProductsService::class.java,
        ProductsService.RAILS_API
    )

    fun getByName(name: String,
                  onSuccess: (response: List<Product>) -> Unit = { _ -> },
                  onFailure: (error: String?) -> Unit = {_ -> }
    ) {
        val token = getToken()

        service.getByName(token, name).enqueue(object : CustomCallback<List<Product>>(app) {
            override fun onSuccess(call: Call<List<Product>>, response: Response<List<Product>>) {
                if (response.isSuccessful) {
                    val body = response.body() as List<Product>

                    Log.d(TAG, "Fetched successfully: $body")
                    onSuccess(body)
                } else {
                    val error = "Fetching failed: ${response.message()}"
                    Log.e(TAG, error)
                    onFailure(error)
                }
            }

            override fun onFailure(call: Call<List<Product>>, t: Throwable) {
                val error = "Could not fetch products. Error: ${t.message}"
                Log.e(TAG, error, t)
                onFailure(error)
            }
        })
    }

    private fun getToken(): String {
        val token = sessionManager.getAuthToken()

        if (token.isNullOrEmpty()) {
            Log.e(TAG, "Null or empty token. Starting LOGIN Activity")

            val intent = Intent(app, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            app.startActivity(intent)

            return ""
        }

        return "Bearer $token"
    }

    companion object {
        const val TAG = "ProductsModel"
    }
}