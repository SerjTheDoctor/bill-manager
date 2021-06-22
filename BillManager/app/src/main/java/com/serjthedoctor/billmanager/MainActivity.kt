package com.serjthedoctor.billmanager

import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.media.ExifInterface
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.widget.ProgressBar
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.net.toUri
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.snackbar.Snackbar
import com.serjthedoctor.billmanager.adapter.BillsAdapter
import com.serjthedoctor.billmanager.databinding.ActivityMainBinding
import com.serjthedoctor.billmanager.domain.Bill
import com.serjthedoctor.billmanager.domain.BillStatus
import com.serjthedoctor.billmanager.model.BillsModel
import java.io.File

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private lateinit var model: BillsModel
    private lateinit var adapter: BillsAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        model = ViewModelProvider(this).get(BillsModel::class.java)

        setupRecyclerView(binding.billsList)
        loadBills()

        binding.refreshButton.setOnClickListener { loadBills() }

        binding.takePictureButton.setOnClickListener {
            remarkDialog {
                val intent = Intent(application, ReceiptScannerActivity::class.java)
                startActivityForResult(intent, RECEIPT_SCANNER_ACTIVITY)
            }
        }

        binding.uploadImageButton.setOnClickListener {
            remarkDialog {
                val intent = Intent(Intent.ACTION_PICK)
                intent.type = "image/*"
                startActivityForResult(intent, IMAGE_FROM_GALLERY)
            }
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
                    Snackbar.make(binding.root, "Receipt not yet processed", Snackbar.LENGTH_SHORT)
                }
            }
        }, object : BillsAdapter.OnLongClickItemListener {
            override fun onLongClickItem(b: Bill) {
                AlertDialog.Builder(this@MainActivity)
                    .setMessage("Are you sure you want to bill from ${b.merchant}?")
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
        binding.progressBar.visibility = ProgressBar.VISIBLE
        model.getBills(
            onSuccess = { bills ->
                adapter.setItems(bills)
                binding.progressBar.visibility = ProgressBar.INVISIBLE
            },
            onFailure = { error ->
                Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
                binding.progressBar.visibility = ProgressBar.INVISIBLE
            }
        )
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
        }
    }

    companion object {
        const val TAG = "MainActivity"
        const val JPG_FILE_SUFFIX = ".jpeg"
        const val RECEIPT_IMAGE_PREFIX = "phone-"
        const val RECEIPT_SCANNER_ACTIVITY = 1
        private const val IMAGE_FROM_GALLERY = 2
        const val DETAILS_ACTIVITY = 3
    }
}
