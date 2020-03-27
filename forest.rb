# ruby forest.rb --count 1000 --tier 1 "cyber physical system" "blockchain"

require 'optparse'

require './invoke-api'
require './func'

params = ARGV.getopts(
  '',
  'count:1000',
  'rank:100',
  'tier:1',
  'input-dir:'
)

p_count = params['count'].to_i
p_rank = params['rank'].to_i
p_tier = params['tier'].to_i
f_input_dir = params['input-dir'].nil? ? false : true
p_input_dir = f_input_dir ? params['input-dir'] : nil

keyword = Array.new
ARGV.each do |val|
  keyword << val
end

result = ''
unless f_input_dir

  # ------------------------------------------
  # read keyword for title and study field
  # ------------------------------------------
  title_keyword = 'And('
  field_keyword = 'Composite(And('
  keyword.each { |v1|
    field_keyword << "F.FN=='#{v1}',"
    v1.split.each { |v2|
      title_keyword << "W=='#{v2}',"
    }
  }
  title_keyword[-1] = ')'
  field_keyword[-1] = '))'
  keyword = "Or(#{title_keyword},#{field_keyword})"

  # ----------------------------------
  # read attributes
  # ----------------------------------
  attributes = read_attributes("asset/attributes")

  # ----------------------------------
  # invoke rest api (tier0)
  # ----------------------------------
  result = invoke_evaluate(expr: keyword, count: p_count, attributes: attributes)
  File.open('./cache/tier0.json', 'w') { |f|
    f.puts JSON.pretty_generate(result)
  }

else

  puts "read file"
  result = JSON.parse(File.read("#{p_input_dir}/tier0.json"))

end

papers = Hash.new
forest = Hash.new

p_tier.times { |i|
  evaluate(result, papers, forest, 0)
}
