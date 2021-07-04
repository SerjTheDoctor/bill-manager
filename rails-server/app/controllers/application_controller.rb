class ApplicationController < ActionController::Base
  protect_from_forgery with: :null_session

  private

  def token(user_id)
    payload = { user_id: user_id, exp: 2.hours.from_now.to_i }
    JWT.encode(payload, hash_secret, hash_algorithm)
  end

  def require_login
    render json: { errors: ['Unauthorized'] }, status: :unauthorized if !client_has_valid_token?
  end

  def hash_secret
    ENV["API_SECRET"]
  end

  def hash_algorithm
    'HS256'
  end

  def client_has_valid_token?
    !!current_user_id
  end

  def current_user_id
    token = request.headers["Authorization"] # Bearer ey...
    token = token.split(' ').second
    
    decoded_array = JWT.decode(token, hash_secret, true, { algorithm: hash_algorithm })
    payload = decoded_array.first
    
    payload['user_id']
  rescue #JWT::VerificationError
    nil
  end
end
