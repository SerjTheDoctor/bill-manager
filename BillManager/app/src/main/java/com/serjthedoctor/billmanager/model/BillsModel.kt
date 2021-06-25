package com.serjthedoctor.billmanager.model

import android.app.Application
import android.content.Intent
import android.util.Log
import android.widget.Toast
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.serjthedoctor.billmanager.LoginActivity
import com.serjthedoctor.billmanager.domain.Bill
import com.serjthedoctor.billmanager.lib.ImageUtils
import com.serjthedoctor.billmanager.service.BillsService
import com.serjthedoctor.billmanager.service.CustomCallback
import com.serjthedoctor.billmanager.service.ServiceFactory
import com.serjthedoctor.billmanager.service.SessionManager
import kotlinx.coroutines.launch
import okhttp3.MediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File

class BillsModel(application: Application) : AndroidViewModel(application) {
    private val app: Application = application
    private val sessionManager: SessionManager = SessionManager(application)
    private val service: BillsService = ServiceFactory.createService(
            BillsService::class.java,
            BillsService.RAILS_API
    )

    fun getBills(
        onSuccess: (response: List<Bill>) -> Unit = {_ -> },
        onFailure: (error: String?) -> Unit = {_ -> }
    ) {
        val token = getToken()

        service.getAll(token).enqueue(object : CustomCallback<List<Bill>>(app) {
            override fun onSuccess(call: Call<List<Bill>>, response: Response<List<Bill>>) {
                if (response.isSuccessful) {
                    val body = response.body() as List<Bill>

                    Log.d(TAG, "Fetched successfully: $body")
                    onSuccess(body)
                } else {
                    val error = "Fetching failed: ${response.message()}"
                    Log.e(TAG, error)
                    onFailure(error)
                }
            }

            override fun onFailure(call: Call<List<Bill>>, t: Throwable) {
                val error = "Could not fetch bills. Error: ${t.message}"
                Log.e(TAG, error, t)
                onFailure(error)
            }
        })
    }

    fun getBill(
        id: Int,
        onSuccess: (response: Bill) -> Unit = {_ -> },
        onFailure: (error: String?) -> Unit = {_ -> }
    ) {
        val token = getToken()

        service.getOne(token, id).enqueue(object : CustomCallback<Bill>(app) {
            override fun onSuccess(call: Call<Bill>, response: Response<Bill>) {
                if (response.isSuccessful) {
                    val body = response.body() as Bill

                    Log.d(TAG, "Fetched one successfully: $body")
                    onSuccess(body)
                } else {
                    val error = "Fetching one with id $id failed: ${response.message()}"
                    Log.e(TAG, error)
                    onFailure(error)
                }
            }

            override fun onFailure(call: Call<Bill>, t: Throwable) {
                val error = "Could not fetch bill with id $id. Error: ${t.message}"
                Log.e(TAG, error, t)
                onFailure(error)
            }
        })
    }

    fun uploadReceiptImage(
        file: File,
        onSuccess: (response: Bill) -> Unit = {_ -> },
        onFailure: (error: String?) -> Unit = {_ -> }
    ) {
        val token = getToken()

        ImageUtils.ensurePortraitImageFile(file)

        // MultipartBody.Part is used to send also the actual file name
        val requestFile = RequestBody.create(MediaType.parse("multipart/form-data"), file)
        val multipartBody = MultipartBody.Part.createFormData("image", file.name, requestFile)

        service.uploadReceipt(token, multipartBody).enqueue(object : CustomCallback<Bill>(app) {
            override fun onSuccess(call: Call<Bill>, response: Response<Bill>) {
                if (response.isSuccessful) {
                    val body = response.body() as Bill

                    Log.d(TAG, "Sent successfully: $body")
                    onSuccess(body)
                } else {
                    val error = "Sending failed: ${response.message()}"
                    Log.e(TAG, error)
                    onFailure(error)
                }
            }

            override fun onFailure(call: Call<Bill>, t: Throwable) {
                val error = "Could not send receipt document. Error: ${t.message}"
                Log.e(TAG, error, t)
                onFailure(error)
            }
        })
    }

    fun updateOne(
        bill: Bill,
        onSuccess: (response: Bill) -> Unit = {_ -> },
        onFailure: (error: String?) -> Unit = {_ -> }
    ) {
        val token = getToken()

        if (bill.id == null) return

        service.updateOne(token, bill.id!!, bill).enqueue(object : CustomCallback<Bill>(app) {
            override fun onSuccess(call: Call<Bill>, response: Response<Bill>) {
                if (response.isSuccessful) {
                    val body = response.body() as Bill

                    Log.d(TAG, "Updated successfully: ${body.id}")
                    onSuccess(body)
                } else {
                    val error = "Update to bill ${bill.id} failed: ${response.message()}"
                    Log.e(TAG, error)
                    onFailure(error)
                }
            }

            override fun onFailure(call: Call<Bill>, t: Throwable) {
                val error = "Could not update bill ${bill.id}. Error: ${t.message}"
                Log.e(TAG, error, t)
                onFailure(error)
            }
        })
    }

    fun deleteBill(
        bill: Bill,
        onSuccess: (response: Bill) -> Unit = {_ -> },
        onFailure: (error: String?) -> Unit = {_ -> }
    ) {
        val token = getToken()

        if (bill.id == null) {
            return
        }

        service.deleteOne(token, bill.id!!).enqueue(object : CustomCallback<Bill>(app) {
            override fun onSuccess(call: Call<Bill>, response: Response<Bill>) {
                if (response.isSuccessful) {
                    val body = response.body() as Bill

                    Log.d(TAG, "Removed successfully: ${body.id}")
                    onSuccess(body)
                } else {
                    val error = "Removing bill ${bill.id} failed: ${response.message()}"
                    Log.e(TAG, error)
                    onFailure(error)
                }
            }

            override fun onFailure(call: Call<Bill>, t: Throwable) {
                val error = "Could not remove bill ${bill.id}. Error: ${t.message}"
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
        const val TAG = "BillsModel"
    }
}