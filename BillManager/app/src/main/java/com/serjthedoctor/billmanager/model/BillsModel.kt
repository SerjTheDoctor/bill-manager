package com.serjthedoctor.billmanager.model

import android.app.Application
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.serjthedoctor.billmanager.lib.ImageUtils
import com.serjthedoctor.billmanager.service.BillsService
import com.serjthedoctor.billmanager.service.ServiceFactory
import kotlinx.coroutines.launch
import okhttp3.MediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody
import java.io.File

class BillsModel(application: Application) : AndroidViewModel(application) {
    private val service: BillsService = ServiceFactory.createService(
            BillsService::class.java,
            BillsService.FLASK_API
    )

    fun uploadReceiptImage(file: File) {
        viewModelScope.launch {
            ImageUtils.ensurePortraitImageFile(file)

            val requestFile = RequestBody.create(MediaType.parse("multipart/form-data"), file)

            // MultipartBody.Part is used to send also the actual file name
            val body = MultipartBody.Part.createFormData("image", file.name, requestFile)
            try {
                val response = service.uploadReceipt(body)
                response.date?.let { Log.d(TAG, it) }
            }
            catch (e: Exception) {
                Log.e(TAG, e.message.toString(), e)
            }
        }
    }

    companion object {
        const val TAG = "BillsModel"
    }
}