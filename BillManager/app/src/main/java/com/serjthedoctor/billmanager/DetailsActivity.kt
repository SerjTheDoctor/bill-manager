package com.serjthedoctor.billmanager

import android.app.DatePickerDialog
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.serjthedoctor.billmanager.adapter.ItemsAdapter
import com.serjthedoctor.billmanager.databinding.ActivityDetailsBinding
import com.serjthedoctor.billmanager.domain.Bill
import com.serjthedoctor.billmanager.model.BillsModel
import kotlinx.android.synthetic.main.activity_details.*
import kotlinx.android.synthetic.main.activity_main.view.*
import java.util.*


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

        backButton.setOnClickListener {
            finish()
        }
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
        binding.deTitle.text = bill.name
        binding.deName.setText(bill.name)
        binding.deMerchant.setText(bill.merchant)
        binding.deTotal.setText(bill.price.toString())

        binding.deName.setOnFocusChangeListener { view, b ->
            if (!b) binding.deTitle.text = binding.deName.text
        }

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