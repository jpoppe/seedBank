# A simple example which could be used for testing seedBank Puppet manifest functionality

file {'/seedBank_puppet_manifest_example':
  ensure  => present,
  content => "seedBank Puppet Manifest Example\n",
  owner   => 'root',
  group   => 'root',
  mode    => 0644;
}
