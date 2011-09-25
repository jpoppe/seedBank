require 'facter'

Facter.add("broadcast") do

  setcode do
    output = %x{ip addr}.grep(/#{Facter.ipaddress}/)[0]
    output =~ /.*?brd\s+(\d+\.\d+\.\d+\.\d+)/
    $1
  end

end
