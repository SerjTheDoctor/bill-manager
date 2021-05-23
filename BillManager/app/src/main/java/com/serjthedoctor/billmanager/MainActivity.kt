package com.serjthedoctor.billmanager

import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.media.ExifInterface
import android.net.Uri
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.core.net.toUri
import androidx.lifecycle.ViewModelProvider
import com.serjthedoctor.billmanager.databinding.ActivityMainBinding
import com.serjthedoctor.billmanager.model.BillsModel
import java.io.File


private const val RECEIPT_SCANNER_ACTIVITY = 1
private const val IMAGE_FROM_GALLERY = 2

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private lateinit var model: BillsModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        model = ViewModelProvider(this).get(BillsModel::class.java)

        binding.takePictureButton.setOnClickListener {
            val intent = Intent(application, ReceiptScannerActivity::class.java)
            startActivityForResult(intent, RECEIPT_SCANNER_ACTIVITY)
        }

        binding.uploadImageButton.setOnClickListener {
            val intent = Intent(Intent.ACTION_PICK)
            intent.type = "image/*"
            startActivityForResult(intent, IMAGE_FROM_GALLERY)
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == IMAGE_FROM_GALLERY && resultCode == RESULT_OK && data != null) {
            data.data?.let { uploadFile(it) }
        }
    }

    private fun uploadFile(uri: Uri) {
        val file = File.createTempFile(RECEIPT_IMAGE_PREFIX, JPG_FILE_SUFFIX)

        val uriStream = contentResolver.openInputStream(uri)
        val fileStream = file.outputStream()
        val bytes = uriStream?.copyTo(fileStream)
        uriStream?.close()
        fileStream.flush()
        fileStream.close()
        Log.d(TAG, "Wrote $bytes bytes to file ${file.absolutePath}")

        model.uploadReceiptImage(file)
    }

    companion object {
        const val TAG = "MainActivity"
        const val JPG_FILE_SUFFIX = ".jpeg"
        const val RECEIPT_IMAGE_PREFIX = "phone-"
    }
}
