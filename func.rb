Paper = Struct.new(
  :title,          # paper title (String)
  :id,             # paper id (Integer)
  :author,         # list of author (Author Struct)
  :citation_count, # number of times cited (Integer)
  :abstract,       # abstract (String)
  :conference,     # conference (Conference Struct)
  :journal,        # journal (Journal Struct)
  :reference,      # list of reference
  :tier
)
Author = Struct.new(
  :name,
  :affiliation
)
Conference = Struct.new(
  :id,
  :name
)
Journal = Struct.new(
  :id,
  :name
)
Publication = Struct.new(
  :type,
  :name_full,
  :name_short,
  :publisher,
  :volume,
  :year
)

def read_attributes(_path)

  attributes = ''
  File.foreach(_path) { |l|
    next if l.start_with?('//')
    next if l.length == 0
    attributes << "#{l.chomp},"
  }

  return attributes.chop

end

def abstract(_ia)

  return "" if _ia.nil?

  tmp = Array.new(_ia['IndexLength'])

  _ia['InvertedIndex'].each { |k,v|
    v.each { |i| tmp[i] = k }
  }

  return tmp.join(' ')

end

#
def parse_entity(_e, _p)

  _p['title'] = _e['DN']

  _p['id'] = _e['Id']

  num_author = _e['AA'].length
  authors = Array.new(num_author)
  _e['AA'].each { |a|
    index = a['S'] - 1 # index start from 1
    authors[index] = Author.new(a['DAuN'], a['DAfN'])
  }
  _p['author'] = authors

  _p['citation_count'] = _e['CC']

  _p['abstract'] = abstract(_e['IA'])

  c = _e['C']
  _p['conference'] = c.nil? ? Conference.new : Conference.new(c['CId'], c['CN']) 

  j = _e['J']
  _p['journal'] = j.nil? ? Journal.new : Journal.new(j['JId'], j['JN'])

  _p['reference'] = _e['RId']

end

def evaluate(_json, _papers, _forest, _tier)

  entities = _json['entities']

  entities.each_with_index { |e,i|
    # ----------------------
    # process for _papers
    # ----------------------
    if _papers.has_key?(e['Id'])
      # add tier info if _papers has ID
      _papers[e['Id']]['tier'] << _tier
    else
      # create paper if _papers does not have ID
      p = Paper.new
      p['tier'] = Array.new
      p['tier'] << _tier
      parse_entity(e, p)
      _papers[e['Id']] = p
    end
    # ----------------------
    # process for _forest
    # ----------------------
    e['RId'].each { |r| 
      _forest[e['Id']] = Array.new unless _forest.has_key?(e['Id'])
      _forest[e['Id']] << r
    } if e.has_key?('RId')
  }

end
