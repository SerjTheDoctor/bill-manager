package com.serjthedoctor.billmanager

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.ProgressBar
import android.widget.Toast
import androidx.core.widget.addTextChangedListener
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.serjthedoctor.billmanager.adapter.ProductsAdapter
import com.serjthedoctor.billmanager.databinding.ActivityProductsBinding
import com.serjthedoctor.billmanager.lib.DebouncingSearchTextListener
import com.serjthedoctor.billmanager.model.ProductsModel

class ProductsActivity : AppCompatActivity() {
    private lateinit var binding: ActivityProductsBinding
    private lateinit var model: ProductsModel
    private lateinit var adapter: ProductsAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProductsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        model = ViewModelProvider(this).get(ProductsModel::class.java)

        setupRecyclerView(binding.prProductsList)

        binding.prBackButton.setOnClickListener {
            finish()
        }

        binding.prSearchItemInput.addTextChangedListener(
            DebouncingSearchTextListener(this@ProductsActivity.lifecycle) { text ->
                if (!text.isNullOrBlank() && text.length > 2) {
                    binding.prProgressBar.visibility = ProgressBar.VISIBLE
                    model.getByName(text,
                        onSuccess = { products ->
                            binding.prProgressBar.visibility = ProgressBar.INVISIBLE
                            adapter.setProducts(products)
                        },
                        onFailure = { error ->
                            Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
                            binding.prProgressBar.visibility = ProgressBar.INVISIBLE
                        }
                    )
                }
            }
        )
    }

    private fun setupRecyclerView(recyclerView: RecyclerView) {
        adapter = ProductsAdapter()
        recyclerView.adapter = adapter
        recyclerView.layoutManager = LinearLayoutManager(this)
    }

    companion object {
        const val TAG = "ProductsActivity"
    }
}