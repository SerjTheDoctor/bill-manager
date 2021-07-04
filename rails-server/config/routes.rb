Rails.application.routes.draw do
  # For details on the DSL available within this file, see https://guides.rubyonrails.org/routing.html
  default_url_options :host => "#{ENV['IP']}:#{ENV['RAILS_PORT']}" #"http://192.168.0.126:3000"
  
  post '/auth/login', to: 'auth#login'
  post '/auth/register', to: 'auth#register'
  
  resources :items
  resources :bills
  resources :users

  get '/products', to: 'items#products'
end
