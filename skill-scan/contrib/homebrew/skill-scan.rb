class SkillScan < Formula
  desc "Security scanner for AI agent skills (SKILL.md)"
  homepage "https://github.com/velvet-sojourner/skill-scan"
  url "https://github.com/velvet-sojourner/skill-scan/releases/download/v0.1.0/skill-scan-macos.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000"

  depends_on "python@3.11"

  def install
    bin.install "skill-scan"
  end

  test do
    system "#{bin}/skill-scan", "--help"
  end
end
