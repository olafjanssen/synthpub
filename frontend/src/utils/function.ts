export const formatDate = (isoDate: string | undefined): string => {
	if (!isoDate) {
		return "";
	}

	const date = new Date(isoDate);

	const pad = (n: number) => n.toString().padStart(2, "0");

	const day = pad(date.getDate());
	const month = pad(date.getMonth() + 1);
	const year = date.getFullYear();

	const hours = pad(date.getHours());
	const minutes = pad(date.getMinutes());
	const seconds = pad(date.getSeconds());

	return `${day}/${month}/${year}, ${hours}:${minutes}:${seconds}`;
};

export const hexToAudioUrl = (hex: string, mimeType = "audio/mpeg"): string => {
	const byteArray = new Uint8Array(
		hex.match(/.{1,2}/g)!.map((byte) => parseInt(byte, 16))
	);
	const blob = new Blob([byteArray], { type: mimeType });
	return URL.createObjectURL(blob);
};
