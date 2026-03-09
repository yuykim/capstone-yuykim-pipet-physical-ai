#include "pipet_hand_mark7_driver/serial_port.hpp"

#include <fcntl.h>
#include <sys/select.h>
#include <termios.h>
#include <unistd.h>

#include <cerrno>
#include <cstring>
#include <stdexcept>

namespace pipet_hand_mark7_driver
{

SerialPort::SerialPort(const std::string & device_path, int baud_rate)
: device_path_(device_path), baud_rate_(baud_rate), fd_(-1)
{
}

SerialPort::~SerialPort()
{
  close();
}

SerialPort::SerialPort(SerialPort && other) noexcept
: device_path_(std::move(other.device_path_)),
  baud_rate_(other.baud_rate_),
  fd_(other.fd_)
{
  other.fd_ = -1;
}

SerialPort & SerialPort::operator=(SerialPort && other) noexcept
{
  if (this != &other) {
    close();
    device_path_ = std::move(other.device_path_);
    baud_rate_   = other.baud_rate_;
    fd_          = other.fd_;
    other.fd_    = -1;
  }
  return *this;
}

bool SerialPort::open()
{
  fd_ = ::open(device_path_.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
  if (fd_ < 0) {
    return false;
  }

  // termios 설정: 115200bps, 8-N-1, raw 모드
  struct termios tty;
  if (tcgetattr(fd_, &tty) != 0) {
    ::close(fd_);
    fd_ = -1;
    return false;
  }

  cfsetispeed(&tty, B115200);
  cfsetospeed(&tty, B115200);
  cfmakeraw(&tty);          // raw 모드 (echo 끄기, 특수문자 처리 끄기)

  tty.c_cflag |= (CLOCAL | CREAD);  // 로컬 연결, 수신 활성화
  tty.c_cflag &= ~CSTOPB;           // 스톱 비트 1
  tty.c_cflag &= ~CRTSCTS;          // 하드웨어 흐름 제어 끄기

  tty.c_cc[VMIN]  = 0;  // 최소 수신 바이트 수 (non-blocking)
  tty.c_cc[VTIME] = 0;  // 읽기 타임아웃 (select로 별도 처리)

  if (tcsetattr(fd_, TCSANOW, &tty) != 0) {
    ::close(fd_);
    fd_ = -1;
    return false;
  }

  tcflush(fd_, TCIOFLUSH);  // 버퍼 비우기
  return true;
}

void SerialPort::close()
{
  if (fd_ >= 0) {
    ::close(fd_);
    fd_ = -1;
  }
}

bool SerialPort::is_open() const
{
  return fd_ >= 0;
}

bool SerialPort::write(const uint8_t * data, std::size_t len)
{
  if (!is_open()) {
    return false;
  }

  std::size_t written = 0;
  while (written < len) {
    ssize_t n = ::write(fd_, data + written, len - written);
    if (n < 0) {
      return false;
    }
    written += static_cast<std::size_t>(n);
  }
  return true;
}

std::string SerialPort::read_crlf_line(int timeout_ms)
{
  if (!is_open()) {
    return {};
  }

  std::string line;
  line.reserve(64);
  bool saw_cr = false;

  while (true) {
    fd_set read_fds;
    FD_ZERO(&read_fds);
    FD_SET(fd_, &read_fds);

    const auto deadline_us = static_cast<long>(timeout_ms) * 1000L;
    struct timeval tv;
    tv.tv_sec  = deadline_us / 1'000'000L;
    tv.tv_usec = deadline_us % 1'000'000L;

    int ret = select(fd_ + 1, &read_fds, nullptr, nullptr, &tv);
    if (ret <= 0) {
      // 타임아웃 또는 오류
      return {};
    }

    char c;
    ssize_t n = ::read(fd_, &c, 1);
    if (n <= 0) {
      return {};
    }

    line += c;
    if (saw_cr && c == '\n') {
      break;
    }
    saw_cr = (c == '\r');
  }

  return line;
}

std::string SerialPort::read_line(int timeout_ms)
{
  return read_crlf_line(timeout_ms);
}

}  // namespace pipet_hand_mark7_driver
