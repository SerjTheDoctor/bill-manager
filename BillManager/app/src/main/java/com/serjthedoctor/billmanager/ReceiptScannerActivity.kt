package com.serjthedoctor.billmanager

import android.Manifest
import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.MotionEvent
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import com.serjthedoctor.billmanager.databinding.ActivityReceiptScannerBinding
import com.serjthedoctor.billmanager.lib.ImageAnalyzer
import com.serjthedoctor.billmanager.model.BillsModel
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors


class ReceiptScannerActivity : AppCompatActivity() {
    private var imageCapture: ImageCapture? = null

    private lateinit var binding: ActivityReceiptScannerBinding
    private lateinit var outputDirectory: File
    private lateinit var cameraExecutor: ExecutorService
    private lateinit var model: BillsModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityReceiptScannerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        model = ViewModelProvider(this).get(BillsModel::class.java)

        // Request camera permissions
        if (allPermissionsGranted()) {
            startCamera()
        } else {
            ActivityCompat.requestPermissions(
                this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS
            )
        }

        // Set up the listener for take photo button
        binding.captureButton.setOnClickListener {
            makeButtonUnavailable()
            takePhoto()
        }
        outputDirectory = getOutputDirectory()
        cameraExecutor = Executors.newSingleThreadExecutor()
    }

    @SuppressLint("RestrictedApi")
    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            // Used to bind the lifecycle of cameras to the lifecycle owner
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()

            // Preview
            val preview = Preview.Builder().build()
                .also {
                    it.setSurfaceProvider(binding.viewFinder.createSurfaceProvider())
                }

            // Image Capture
            imageCapture = ImageCapture.Builder().build()

            // Image Analyzer
            // val imageAnalyzer = ImageAnalysis.Builder()
            //     .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            //     .build()
            //     .also {
            //         it.setAnalyzer(cameraExecutor, ImageAnalyzer { visionText, height, width ->
            //             Log.d(TAG, "Detected ${visionText.text}!")
            //             binding.overlay.setRecognizedData(visionText.textBlocks, height, width)
            //         })
            //     }

            try {
                // Unbind use cases before rebinding
                cameraProvider.unbindAll()

                // Bind use cases to camera
                val camera = cameraProvider.bindToLifecycle(
                    this,
                    CAMERA_SELECTOR,
                    imageCapture,
                    preview,
                    // imageAnalyzer
                )

                enableManualFocus(camera.cameraControl)
            } catch (e: Exception) {
                Log.e(TAG, "Use case binding failed", e)
            }

        }, ContextCompat.getMainExecutor(this))


    }

    @SuppressLint("ClickableViewAccessibility")
    private fun enableManualFocus(cameraControl: CameraControl) {
        binding.viewFinder.setOnTouchListener { _: View, motionEvent: MotionEvent ->
            when (motionEvent.action) {
                MotionEvent.ACTION_DOWN -> return@setOnTouchListener true
                MotionEvent.ACTION_UP -> {
                    // Get the MeteringPointFactory from PreviewView
                    val factory = binding.viewFinder.createMeteringPointFactory(CAMERA_SELECTOR)

                    // Create a MeteringPoint from the tap coordinates
                    val point = factory.createPoint(motionEvent.x, motionEvent.y)

                    // Create a MeteringAction from the MeteringPoint, you can configure it to specify the metering mode
                    val action = FocusMeteringAction.Builder(point).build()

                    // Trigger the focus and metering. The method returns a ListenableFuture since the operation
                    // is asynchronous. You can use it get notified when the focus is successful or if it fails.
                    cameraControl.startFocusAndMetering(action)

                    return@setOnTouchListener true
                }
                else -> return@setOnTouchListener false
            }
        }
    }

    private fun takePhoto() {
        // Get a reference of the modifiable image capture
        val imageCapture = imageCapture ?: return

        // Create output file
        val photoFile = File(
            outputDirectory,
            SimpleDateFormat(FILENAME_FORMAT, Locale.US).format(System.currentTimeMillis()) + ".jpg"
        )

        // Output options which contain file + metadata
        val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()

        // Image listener
        imageCapture.takePicture(
            outputOptions,
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                    val url = Uri.fromFile(photoFile)

                    val msg = "Photo was successfully captured: $url"
                    Toast.makeText(baseContext, msg, Toast.LENGTH_SHORT).show()
                    Log.d(TAG, msg)

                    model.uploadReceiptImage(photoFile,
                        onSuccess = {
                            val resultIntent = Intent()
                            setResult(RESULT_OK, resultIntent)
                            finish()
                        },
                        onFailure = { error ->
                            Toast.makeText(
                                this@ReceiptScannerActivity,
                                "Upload error: $error",
                                Toast.LENGTH_LONG
                            ).show()
                            makeButtonAvailable()
                        }
                    )
                }

                override fun onError(e: ImageCaptureException) {
                    Log.e(TAG, "Photo capture failed: ${e.message}", e)
                    makeButtonAvailable()
                }
            }
        )
    }

    private fun makeButtonAvailable() {
        binding.captureButton.isClickable = true
        binding.captureButton.alpha = 1f
    }

    private fun makeButtonUnavailable() {
        binding.captureButton.isClickable = false
        binding.captureButton.alpha = 0.3f
    }

    private fun getOutputDirectory(): File {
        val mediaDir = externalMediaDirs.firstOrNull()?.let {
            File(it, resources.getString(R.string.app_name)).apply { mkdirs() }
        }
        return if (mediaDir != null && mediaDir.exists())
            mediaDir else filesDir
    }

    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<String>, grantResults: IntArray
    ) {
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (allPermissionsGranted()) {
                startCamera()
            } else {
                Toast.makeText(
                    this,
                    "Permissions not granted by the user.",
                    Toast.LENGTH_SHORT
                ).show()
                finish()
            }
        }
    }

    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
    }

    companion object {
        val CAMERA_SELECTOR = CameraSelector.DEFAULT_BACK_CAMERA
        const val TAG = "ReceiptScannerActivity"
        const val FILENAME_FORMAT = "yyyy-MM-dd-HH-mm-ss-SSS"
        const val REQUEST_CODE_PERMISSIONS = 10
        private val REQUIRED_PERMISSIONS = arrayOf(Manifest.permission.CAMERA)
    }
}