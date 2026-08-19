until curl -f -L -C - -o "/mnt/chromeos/shared/removable/Kingston/InstallMacOSX.dmg" "https://updates.cdn-apple.com/2021/macos/041-7683-20210614-E610947E-C7CE-46EB-8860-D26D71F0D3EA/InstallMacOSX.dmg"; do
  echo "Download interrupted or failed. Retrying in 5 seconds..."
  sleep 5
done

7z x "/mnt/chromeos/shared/removable/Kingston/InstallMacOSX.dmg" -o"/mnt/chromeos/shared/removable/Kingston/extracted"

7z x "/mnt/chromeos/shared/removable/Kingston/extracted/InstallOS.pkg" -o"/mnt/chromeos/shared/removable/Kingston/extracted_pkg"

dmg2img -i "/mnt/chromeos/shared/removable/Kingston/extracted_pkg/InstallESD.dmg" -o "/mnt/chromeos/shared/removable/Kingston/InstallMacOSX.bin"

echo "Good."
exit 0

echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# 1. Download official DMG payload
curl -L -o "/mnt/chromeos/shared/removable/Kingston/InstallMacOSX.dmg" "https://updates.cdn-apple.com/2021/macos/041-7683-20210614-E610947E-C7CE-46EB-8860-D26D71F0D3EA/InstallMacOSX.dmg"

# 2. Extract outer DMG
7z x "/mnt/chromeos/shared/removable/Kingston/InstallMacOSX.dmg" -o"/mnt/chromeos/shared/removable/Kingston/extracted"

# 3. Extract the inner PKG file (Note: The payload inside is named InstallOS.pkg)
7z x "/mnt/chromeos/shared/removable/Kingston/extracted/InstallOS.pkg" -o"/mnt/chromeos/shared/removable/Kingston/extracted_pkg"

# 4. Decompress InstallESD.dmg to .bin (skipping the extra .img mv step)
dmg2img -i "/mnt/chromeos/shared/removable/Kingston/extracted_pkg/InstallESD.dmg" -o "/mnt/chromeos/shared/removable/Kingston/InstallMacOSX.bin"