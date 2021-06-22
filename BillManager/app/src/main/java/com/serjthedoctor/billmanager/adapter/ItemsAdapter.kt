package com.serjthedoctor.billmanager.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.serjthedoctor.billmanager.R
import com.serjthedoctor.billmanager.domain.Item

class ItemsAdapter : RecyclerView.Adapter<ItemsAdapter.ItemsViewHolder>() {
    private var items = mutableListOf<Item>()

    inner class ItemsViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val namee: TextView = view.findViewById(R.id.deItemName)
        val quantity: TextView = view.findViewById(R.id.deItemQuantity)
        val unit: TextView = view.findViewById(R.id.deItemUnit)
        val unitPrice: TextView = view.findViewById(R.id.deItemUnitPrice)
        // val price: TextView = view.findViewById(R.id.deItemPrice)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ItemsViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.items_list_item, parent, false)
        return ItemsViewHolder(view)
    }

    override fun onBindViewHolder(holder: ItemsViewHolder, position: Int) {
        val item = items[position]

        holder.namee.text = item.name
        holder.quantity.text = item.quantity.toString()
        holder.unit.text = item.unit
        holder.unitPrice.text = item.unitPrice.toString()
        // holder.price.text = item.price.toString()
    }

    override fun getItemCount(): Int = items.size

    fun setItems(newItems: List<Item>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }
}