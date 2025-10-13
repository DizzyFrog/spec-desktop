import { requestClient, baseRequestClient } from '#/api/request';

const API_PREFIX = '/api';

/**
 * @description: Upload excel file
 */
export function uploadExcel(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return requestClient.post(
    {
      url: `${API_PREFIX}/upload/upload`,
      data: formData,
    },
    {
      // Axios-specific options for file upload
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  );
}

/**
 * @description: Process the uploaded excel file
 */
export function processExcel(filePath: string) {
  return requestClient.post({
    url: `${API_PREFIX}/generate/process-excel`,
    data: { file_path: filePath },
  });
}

/**
 * @description: Generate mermaid images in parallel
 */
export function generateMermaidImages(chapters: any[]) {
  return requestClient.post({
    url: `${API_PREFIX}/generate/mermaid-images`,
    data: { chapters },
  });
}

/**
 * @description: Generate the final word document
 */
export async function generateWord(chapters: any[], imageMapping: Record<string, string>) {
  const response = await baseRequestClient.post(
    {
      url: `${API_PREFIX}/generate/generate-word`,
      data: {
        chapters,
        image_mapping: imageMapping,
        output_filename: '需求说明书.docx',
      },
    },
    {
      responseType: 'blob',
    },
  );

  // Trigger file download
  if (response.data) {
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', '需求说明书.docx');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  return response;
}
