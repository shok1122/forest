require 'json'
require 'rest-client'

require './utils'

def concatenation(_str1, _key, _str2, _delim)

  if 0 < "#{_str2}".length then
    str = "#{_key}=#{_str2}"
    return _str1.length == 0 ? str : "#{_str1}&#{str}"
  end
  return _str1

end


#
# REST API(GET)の実行
#
def invoke_evaluate(expr:, model: "latest", count: 10, attributes:)

  options = ""
  options = concatenation(options, "expr", expr, "&")
  options = concatenation(options, "model", model, "&")
  options = concatenation(options, "count", count, "&")
  options = concatenation(options, "attributes", attributes, "&")

  url = "https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?#{options}"

  token = File.read("cache/subscription.key")

  resp = RestClient.get(
    url,
    {
      "content_type": "application/json",
      "Ocp-Apim-Subscription-Key": "#{token}"
    }
  )

  return JSON.parse(resp)
end

# main
if File.basename($PROGRAM_NAME) == File.basename(__FILE__)

  if ARGV.size.zero?
    Utils::log_err 'no args'
    return nil
  end

  expr = "#{ARGV[0]}"
  model = "#{ARGV[1]}"
  count = "#{ARGV[2]}"
  attributes = "#{ARGV[3]}"

  result = invoke_evaluate(expr, model, count.to_i < 0 ? nil : count, attributes)

  #File.open("#{path.gsub('/','_')}.json", 'w') do |f|
  #  JSON.dump(result, f)
  #end
end