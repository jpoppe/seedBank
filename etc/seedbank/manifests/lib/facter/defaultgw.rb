require 'facter'

Facter.add("defaultgw") do

  setcode do
    output = %x{ip route show 0.0.0.0/0}.chomp
    result = output.split(' ')
    result[2]
  end

end
