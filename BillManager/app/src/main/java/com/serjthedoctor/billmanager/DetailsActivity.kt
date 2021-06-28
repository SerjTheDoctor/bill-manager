package com.serjthedoctor.billmanager

import android.annotation.SuppressLint
import android.app.DatePickerDialog
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.resource.bitmap.RoundedCorners
import com.bumptech.glide.request.RequestOptions
import com.serjthedoctor.billmanager.adapter.ItemsAdapter
import com.serjthedoctor.billmanager.databinding.ActivityDetailsBinding
import com.serjthedoctor.billmanager.domain.Bill
import com.serjthedoctor.billmanager.domain.BillStatus
import com.serjthedoctor.billmanager.lib.limit
import com.serjthedoctor.billmanager.model.BillsModel
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.*
import kotlin.math.abs


class DetailsActivity : AppCompatActivity() {
    private lateinit var binding: ActivityDetailsBinding
    private lateinit var model: BillsModel
    private lateinit var bill: Bill
    private lateinit var recyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDetailsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        model = ViewModelProvider(this).get(BillsModel::class.java)

        recyclerView = binding.itemsRecyclerView

        if (intent.hasExtra(BILL_ID)) {
            val billId = intent.extras?.getInt(BILL_ID)

            if (billId != null) {
                loadBillDetails(billId)
            }
        }

        binding.backButton.setOnClickListener {
            finish()
        }
        binding.saveButton.setOnClickListener {
            saveBillDetails()
        }
    }

    @SuppressLint("NewApi")
    private fun saveBillDetails() {
        bill.name = binding.deName.text.toString()
        bill.merchant = binding.deMerchant.text.toString()

        val formatter = DateTimeFormatter.ofPattern("d/M/yyyy")
        val localDate = LocalDate.parse(binding.deDate.text.toString(), formatter)
        bill.date = localDate

        bill.price = binding.deTotal.text.toString().toFloat()

        model.updateOne(bill,
            onSuccess = {
                val resultIntent = Intent()
                setResult(RESULT_OK, resultIntent)
                finish()
            },
            onFailure = {
                Toast.makeText(
                    this@DetailsActivity,
                    "Update error: $it",
                    Toast.LENGTH_LONG
                ).show()
            }
        )
    }

    private fun loadBillDetails(billId: Int) {
        model.getBill(billId,
            onSuccess = {
                bill = it
                populate()
                setupItemsRecyclerView()
            },
            onFailure = { error ->
                Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
            }
        )
    }

    private fun populate() {
        binding.deTitle.text = bill.name?.limit(20)
        binding.deName.setText(bill.name)
        binding.deMerchant.setText(bill.merchant)

        // when name input losses focus, update the title
        binding.deName.setOnFocusChangeListener { _, focused ->
            if (!focused) binding.deTitle.text = binding.deName.text
        }

        when (bill.status) {
            BillStatus.QUEUED -> binding.deStatus.setTextColor(Color.RED)
            BillStatus.RUNNING -> binding.deStatus.setTextColor(Color.parseColor("#CCCC00"))
            BillStatus.PROCESSED -> binding.deStatus.setTextColor(Color.GREEN)
            else -> binding.deStatus.setTextColor(Color.BLACK)
        }

        if (bill.status == null) {
            binding.deStatus.text = "-"
        } else {
            binding.deStatus.text = bill.status!!.name
        }

        populateTotalPrice()
        populateDate()
        populateImages()
    }

    private fun populateTotalPrice() {
        binding.deTotal.setText(bill.price.toString())

        binding.deTotal.setOnKeyListener { _, _, _ ->
            if (bill.items != null && !binding.deTotal.text.isNullOrBlank()) {
                try {
                    val totalPrice = binding.deTotal.text.toString().toFloat()
                    val sum = bill.items!!.sumByDouble { (it.price ?: 0).toDouble() }
                    if (abs(totalPrice - sum) > 1) {
                        binding.deTotal.setTextColor(Color.RED)
                    } else {
                        binding.deTotal.setTextColor(Color.BLACK)
                    }
                } catch (e: Exception) {
                    e.message?.let {
                        Log.e("[DetailsActivity/populateTotalPrice] ERROR: ", e.message, e)
                    }
                }
            }
            false
        }

    }

    private fun populateDate() {
        val calendar: Calendar = Calendar.getInstance()
        var day: Int = calendar.get(Calendar.DAY_OF_MONTH)
        var month: Int = calendar.get(Calendar.MONTH)
        var year: Int = calendar.get(Calendar.YEAR)

        if (bill.date != null) {
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                day = bill.date!!.dayOfMonth
                month = bill.date!!.monthValue
                year = bill.date!!.year
            } else {
                day = 1
                month = 1
                year = 2021
            }
        }

        var dateText = "$day/$month/${year}"
        binding.deDate.text = dateText

        binding.deDate.setOnClickListener {
            val picker = DatePickerDialog(
                this@DetailsActivity,
                { _, newYear, monthOfYear, dayOfMonth ->
                    dateText = "$dayOfMonth/${monthOfYear+1}/$newYear"
                    binding.deDate.text = dateText
                },
                year,
                month-1,
                day
            )
            picker.show()
        }
    }

    private fun populateImages() {
        val requestOptions = RequestOptions().transform(RoundedCorners(16))

        Glide.with(this)
            .load(bill.imageUrl)
            .apply(requestOptions)
            .into(binding.deBillImage)

        Glide.with(this)
            .load(bill.imageUrl)
            .apply(requestOptions)
            .into(binding.deBigBillImage)

        binding.deBillImage.setOnClickListener {
            binding.deBigConstraint.visibility = View.VISIBLE
        }
        binding.deBigConstraint.setOnClickListener {
            binding.deBigConstraint.visibility = View.INVISIBLE
        }
    }

    private fun setupItemsRecyclerView() {
        val adapter = ItemsAdapter()
        bill.items?.let { adapter.setItems(it) }

        recyclerView.adapter = adapter
        recyclerView.layoutManager = LinearLayoutManager(this)
    }

    companion object {
        const val BILL_ID = "BILL_ID"
    }
}