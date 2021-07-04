class AuthController < ApplicationController
  def login
    user = User.find_by("lower(email) = ?", login_params[:email].downcase)

    if user && user.authenticate(login_params[:password])
      render json: { token: token(user.id), user: user.permitted }, status: :ok 
    else 
      render json: { errors: [ "Sorry, incorrect email or password" ] }, status: :bad_request
    end 
  end

  def register
    user = User.new(register_params)

    if user.save
      render json: { token: token(user.id), user: user.permitted }, status: :ok
    else
      render json: { errors: user.errors.full_messages.join(', ') }, status: :bad_request
    end
  end

  private 

  def login_params
    keys = %i[email password]
    params.slice(*keys).permit(*keys)
  end

  def register_params
    keys = %i[name email password]
    params.slice(*keys).permit(*keys)
  end
end