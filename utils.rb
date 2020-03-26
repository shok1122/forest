require 'date'
require 'open3'

class Utils

  @@dest = STDERR

  class << self

    #
    # 出力先の切り替え
    #
    def switch(_dest)
      @@dest = _dest
    end

    #
    # ログ出力
    #
    def log(_attr, _str)
      d = DateTime.now.strftime("%Y%m%d-%H%M%S")
      _str.lines { |l|
        @@dest.puts "#{d} #{_attr} #{l}"
      }
    end

    #
    # ログ(INFO)
    #
    def log_info(_str)
      log('INFO', _str)
    end

    #
    # ログ(ERR)
    #
    def log_err(_str)
      log("\e[31mERR\e[0m ", _str)
    end

    #
    # ログ(CMD)
    #
    def log_cmd(_str)
      log("\e[32mCMD\e[0m ", _str)
    end

    def get_dict(_dct, _key)
      keys = _key.split(':')
      keys.each { |k|
        _dct = _dct[k]
      }
      return _dct
    end

    #
    # コマンド実行
    #
    def run(_cmd)

      log_cmd(_cmd)

      out = ""
      err = ""
      status = ""

      Open3.popen3(_cmd) do |i, o, e, w|
        o.each  { |line|
          log_info(line)
          out += line
        }
        e.each { |line|
          log_err(line)
          err += line
        }
        status = w.value # Process::Status object
      end

      return out,err,status
    end
  end
end