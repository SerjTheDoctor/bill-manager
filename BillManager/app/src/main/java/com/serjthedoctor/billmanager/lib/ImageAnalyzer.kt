package com.serjthedoctor.billmanager.lib

import android.annotation.SuppressLint
import android.util.Log
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.Text
import com.google.mlkit.vision.text.TextRecognition
import com.serjthedoctor.billmanager.ReceiptScannerActivity

typealias VisionTextListener = (text: Text, height: Int, width: Int) -> Unit

class ImageAnalyzer(private val listener: VisionTextListener): ImageAnalysis.Analyzer {
    @SuppressLint("UnsafeExperimentalUsageError")
    override fun analyze(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage != null) {
            val image = InputImage.fromMediaImage(
                mediaImage, imageProxy.imageInfo.rotationDegrees
            )
            val recognizer = TextRecognition.getClient()

            recognizer.process(image)
                .addOnSuccessListener { visionText ->
                    listener(visionText, imageProxy.height, imageProxy.width)
                }
                .addOnFailureListener { e ->
                    Log.e(ReceiptScannerActivity.TAG, "Recognizing process failed", e)
                }
                .addOnCompleteListener {
                    imageProxy.close()
                }
        }
    }
}