package Debian::Debhelper::Buildsystem::python_virtualenv;

use strict;
use Debian::Debhelper::Dh_Lib qw(sourcepackage);
use base 'Debian::Debhelper::Buildsystem';

sub DESCRIPTION {
	"Python Virtualenv (setup.py / requirements.txt)"
}

sub DEFAULT_BUILD_DIRECTORY {
	my $this=shift;
	return $this->canonpath($this->get_sourcepath("build"));
}

sub check_auto_buildable {
	my $this=shift;
	return (-e $this->get_sourcepath("setup.py")) ? 1 : 0;
}

sub new {
	my $class=shift;
	my $this= $class->SUPER::new(@_);
	$this->prefer_out_of_source_building(@_);
	#$this->enforce_in_source_building();
	return $this;
}

sub build {
	my $this=shift;
	$this->doit_in_sourcedir("dh_virtualenv_build", @_);
}

sub install {
	my $this=shift;
	my $destdir=shift;
  $this->doit_in_sourcedir("dh_virtualenv_install",
	  "--package=" . sourcepackage(),
    "--package-dir=$destdir",
    @_);
}

sub clean {
	my $this=shift;
	$this->rmdir_builddir();
}

1
