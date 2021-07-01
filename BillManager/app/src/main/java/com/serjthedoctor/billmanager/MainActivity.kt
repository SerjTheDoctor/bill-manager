package com.serjthedoctor.billmanager

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.util.Log
import android.widget.ProgressBar
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.core.net.toUri
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.snackbar.Snackbar
import com.serjthedoctor.billmanager.adapter.BillsAdapter
import com.serjthedoctor.billmanager.databinding.ActivityMainBinding
import com.serjthedoctor.billmanager.domain.Bill
import com.serjthedoctor.billmanager.domain.BillStatus
import com.serjthedoctor.billmanager.lib.DebouncingSearchTextListener
import com.serjthedoctor.billmanager.model.BillsModel
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private lateinit var model: BillsModel
    private lateinit var adapter: BillsAdapter
    private lateinit var currentPhotoPath: String
    private lateinit var allBills: List<Bill>
    private var seenRemark = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        model = ViewModelProvider(this).get(BillsModel::class.java)

        setupRecyclerView(binding.billsList)
        loadBills()

        binding.searchProductsButton.setOnClickListener {
            val intent = Intent(application, ProductsActivity::class.java)
            startActivityForResult(intent, PRODUCTS_ACTIVITY)
        }

        binding.refreshButton.setOnClickListener { loadBills() }

        binding.searchBillInputText.addTextChangedListener(
            DebouncingSearchTextListener(this@MainActivity.lifecycle, debounceTime = 100) { text ->
                adapter.setItems(filterBills(text))
            }
        )

        binding.takePictureButton.setOnClickListener {
            if (seenRemark) {
                openCamera()
            } else {
                remarkDialog {
                    seenRemark = true
                    openCamera()
                }
            }
        }

        binding.uploadImageButton.setOnClickListener {
            if (seenRemark) {
                val intent = Intent(Intent.ACTION_PICK)
                intent.type = "image/*"
                startActivityForResult(intent, IMAGE_FROM_GALLERY)
            } else {
                remarkDialog {
                    seenRemark = true
                    val intent = Intent(Intent.ACTION_PICK)
                    intent.type = "image/*"
                    startActivityForResult(intent, IMAGE_FROM_GALLERY)
                }
            }
        }
    }

    private fun openCamera() {
        if (allPermissionsGranted()) {
            dispatchTakePictureIntent()
        } else {
            ActivityCompat.requestPermissions(
                this,
                REQUIRED_PERMISSIONS,
                REQUEST_CODE_PERMISSIONS
            )
        }
    }

    private fun remarkDialog(continuation: () -> Unit) {
        AlertDialog.Builder(this)
            .setMessage("Please make sure that the photo covers all the receipt and the background is in high contrast with the document")
            .setPositiveButton("Continue") { _, _ -> continuation()}
            .setNegativeButton("Cancel") { dialog, _ -> dialog.dismiss()}
            .create()
            .show()
    }

    private fun setupRecyclerView(recyclerView: RecyclerView) {
        adapter = BillsAdapter(object : BillsAdapter.OnClickItemListener {
            override fun onClickItem(b: Bill) {
                if (b.status == BillStatus.PROCESSED) {
                    val detailsIntent = Intent(application, DetailsActivity::class.java)
                    detailsIntent.putExtra(DetailsActivity.BILL_ID, b.id)
                    startActivityForResult(detailsIntent, DETAILS_ACTIVITY)
                } else {
                    Snackbar.make(binding.root, "Receipt has no details", Snackbar.LENGTH_SHORT).show()
                }
            }
        }, object : BillsAdapter.OnLongClickItemListener {
            override fun onLongClickItem(b: Bill) {
                AlertDialog.Builder(this@MainActivity)
                    .setMessage("Are you sure you want to remove ${b.merchant}?")
                    .setPositiveButton("Continue") { _, _ ->
                        Log.d(TAG, "Will delete ${b.merchant}")

                        model.deleteBill(b,
                            onSuccess = { loadBills() },
                            onFailure = { error ->
                                Toast.makeText(this@MainActivity, error, Toast.LENGTH_LONG).show()
                            }
                        )
                    }
                    .setNegativeButton("Cancel") { dialog, _ -> dialog.dismiss()}
                    .create()
                    .show()
            }
        })
        recyclerView.adapter = adapter
        recyclerView.layoutManager = LinearLayoutManager(this)
    }

    private fun loadBills() {
        binding.searchBillInputText.setText("")
        binding.progressBar.visibility = ProgressBar.VISIBLE
        model.getBills(
            onSuccess = { bills ->
                allBills = bills
                adapter.setItems(bills)
                binding.progressBar.visibility = ProgressBar.INVISIBLE
            },
            onFailure = { error ->
                Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
                binding.progressBar.visibility = ProgressBar.INVISIBLE
            }
        )
    }

    private fun filterBills(query: String?) : List<Bill> {
        if (query.isNullOrBlank() || query.isEmpty()) return allBills

        val filteredBills = mutableListOf<Bill>()

        for (bill in allBills) {
            if (bill.name?.toLowerCase(Locale.ROOT)?.contains(query.toLowerCase(Locale.ROOT)) == true ||
                bill.merchant?.toLowerCase(Locale.ROOT)?.contains(query.toLowerCase(Locale.ROOT)) == true) {
                filteredBills.add(bill)
            }
        }

        return filteredBills
    }

    private fun dispatchTakePictureIntent() {
        val intent = Intent(application, ReceiptScannerActivity::class.java)
        startActivityForResult(intent, RECEIPT_SCANNER_ACTIVITY)

        // Intent(MediaStore.ACTION_IMAGE_CAPTURE).also { takePictureIntent ->
        //     // Ensure that there's a camera activity to handle the intent
        //     takePictureIntent.resolveActivity(packageManager)?.also {
        //         // Create the File where the photo should go
        //         val photoFile: File? = try {
        //             createImageFile()
        //         } catch (ex: IOException) {
        //             // Error occurred while creating the File
        //             null
        //         }
        //         // Continue only if the File was successfully created
        //         photoFile?.also {
        //             val photoURI: Uri = FileProvider.getUriForFile(
        //                 this,
        //                 "com.serjthedoctor.billmanager",
        //                 it
        //             )
        //             takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI)
        //             startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE)
        //         }
        //     }
        // }
    }

    private fun createImageFile(): File {
        // Create an image file name
        val timeStamp: String = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.ROOT).format(Date())
        val storageDir: File? = getExternalFilesDir(Environment.DIRECTORY_PICTURES)

        return File.createTempFile(
            "JPEG_${timeStamp}_", /* prefix */
            ".jpg", /* suffix */
            storageDir /* directory */
        ).apply {
            // Save a file: path for use with ACTION_VIEW intents
            currentPhotoPath = absolutePath
        }
    }

    private fun getFile(uri: Uri): File {
        val file = File.createTempFile(RECEIPT_IMAGE_PREFIX, JPG_FILE_SUFFIX)

        val uriStream = contentResolver.openInputStream(uri)
        val fileStream = file.outputStream()
        val bytes = uriStream?.copyTo(fileStream)
        uriStream?.close()
        fileStream.flush()
        fileStream.close()
        Log.d(TAG, "Wrote $bytes bytes to file ${file.absolutePath}")

        return file
    }

    private fun uploadFile(file: File) {
        model.uploadReceiptImage(file,
            onSuccess = { bill ->
                Toast.makeText(this, "Processed bill ${bill.id}", Toast.LENGTH_SHORT).show()
                loadBills()
            },
            onFailure = { msg ->
                Toast.makeText(this, "Error: $msg", Toast.LENGTH_LONG).show()
            }
        )
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == IMAGE_FROM_GALLERY && resultCode == RESULT_OK && data != null) {
            data.data?.let {
                val file = getFile(it)
                uploadFile(file)
            }
        } else if (requestCode == RECEIPT_SCANNER_ACTIVITY && resultCode == RESULT_OK) {
            loadBills()
        } else if (requestCode == DETAILS_ACTIVITY && resultCode == RESULT_OK) {
            loadBills()
        } else if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_OK) {
            Toast.makeText(this, "Took photo at $currentPhotoPath", Toast.LENGTH_SHORT).show()
            val file = File(currentPhotoPath)
            uploadFile(file)
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<String>, grantResults: IntArray
    ) {
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (allPermissionsGranted()) {
                dispatchTakePictureIntent()
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

    companion object {
        const val TAG = "MainActivity"
        const val JPG_FILE_SUFFIX = ".jpeg"
        const val RECEIPT_IMAGE_PREFIX = "phone-"
        const val RECEIPT_SCANNER_ACTIVITY = 1
        private const val IMAGE_FROM_GALLERY = 2
        const val DETAILS_ACTIVITY = 3
        const val PRODUCTS_ACTIVITY = 4
        const val REQUEST_IMAGE_CAPTURE = 5
        const val REQUEST_CODE_PERMISSIONS = 100
        private val REQUIRED_PERMISSIONS = arrayOf(Manifest.permission.CAMERA)
    }
}
