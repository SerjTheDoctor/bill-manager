package com.serjthedoctor.billmanager.adapter

import android.annotation.SuppressLint
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.serjthedoctor.billmanager.R
import com.serjthedoctor.billmanager.domain.Item
import com.serjthedoctor.billmanager.domain.Product
import com.serjthedoctor.billmanager.lib.limit
import java.time.format.DateTimeFormatter
import java.util.*

class ProductsAdapter : RecyclerView.Adapter<ProductsAdapter.ProductsViewHolder>() {
    private var products = mutableListOf<Product>()

    inner class ProductsViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val name: TextView = view.findViewById(R.id.prItemName)
        val merchant: TextView = view.findViewById(R.id.prItemMerchant)
        val date: TextView = view.findViewById(R.id.prItemDate)
        val unitPrice: TextView = view.findViewById(R.id.prItemUnitPrice)
        val unit: TextView = view.findViewById(R.id.prItemUnit)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProductsAdapter.ProductsViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.products_list_item, parent, false)
        return ProductsViewHolder(view)
    }

    @SuppressLint("NewApi")
    override fun onBindViewHolder(holder: ProductsAdapter.ProductsViewHolder, position: Int) {
        val p = products[position]

        holder.name.text = p.name?.capitalize(Locale.ROOT)?.limit(30) ?: "-"
        holder.unitPrice.text = p.unitPrice?.toString() ?: "N/A"
        holder.unit.text = if (p.unit != null) "per ${p.unit?.capitalize(Locale.ROOT)}" else ""

        if (p.merchant == null) {
            holder.merchant.visibility = View.GONE
        } else {
            holder.merchant.text = p.merchant!!.capitalize(Locale.ROOT).limit(20)
        }

        if (p.date == null) {
            holder.date.visibility = View.GONE
        } else {
            val pattern = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                if (p.date!!.year == Calendar.getInstance().get(Calendar.YEAR)) {
                    "dd MMMM"
                } else {
                    "dd MMMM yyyy"
                }
            } else {
                "dd MMMM yyyy"
            }
            holder.date.text = p.date!!.format(DateTimeFormatter.ofPattern(pattern))
        }
    }

    override fun getItemCount(): Int = products.size

    fun setProducts(newProducts: List<Product>) {
        products.clear()
        products.addAll(newProducts)
        notifyDataSetChanged()
    }
}