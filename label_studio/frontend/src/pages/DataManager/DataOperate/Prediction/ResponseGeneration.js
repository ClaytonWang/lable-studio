import React, { useCallback, useEffect } from 'react';
import { Form, InputNumber } from 'antd';
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { Select } from '@/components/Form';
import { PromptTemplate } from "@/components/PromptTemplate/PromptTemplate";
import { useAPI } from '@/providers/ApiProvider';

const formItemLayout = {
  labelCol: { span: 4 },
  wrapperCol: { span: 20 },
};

const ResponseGeneration = ({ close, execLabel, loading, project }) => {
  const [execModel, setExecModel] = React.useState('');
  const [execModelList, setExecModelList] = React.useState([]);
  const api = useAPI();

  const getModelList = useCallback(async () => {
    const rslt = await api.callApi("modelManager", {
      params: {
        project_id: project.id,
      },
    });

    const data = rslt?.results ?? [];

    setExecModelList([{ id:'',title:'请选择模型',version:'',value:'' },...data]);

  }, []);

  useEffect(() => {
    getModelList();
  }, []);

  const onFinish = useCallback((values) => {
    execLabel(values);
  }, [execLabel]);

  return (
    <>
      <Modal.Header>
      对话生成(普通)
      </Modal.Header>
      <Form
        {...formItemLayout}
        onFinish={onFinish}
      >
        <Form.Item
          name="model_id"
          label="选择模型"
          validateStatus={execModel ? 'success' : 'error'}
          help={!execModel ? "请选择模型" : ''}
          rules={[{ required: true, message: t('tip_please_complete') }]}
        >
          <div style={{ width: 300 }}>
            <Select
              options={execModelList?.map(v => {
                return { label: v.title + v.version, value: v.id };
              })}
              onChange={(e) => {
                setExecModel(e.target.value);
              }} />
          </div>
        </Form.Item>
        <Form.Item
          name="generate_count"
          label="生成回答数量"
          initialValue={1}
          rules={[{ required: true, message: t('tip_please_complete') }]}
        >
          <InputNumber max={100} min={1} />
        </Form.Item>
        <Form.Item
          name="templates"
          label="提示学习">
          <PromptTemplate project={project} tag />
        </Form.Item>
        <Modal.Footer>
          <Space align="end">
            <Button
              size="compact"
              onClick={(e) => { e.preventDefault(); close();}}
            >
              {t("Cancel")}
            </Button>
            <Button
              size="compact"
              look="primary"
              type="submit"
              waiting={loading}
              disabled={ !execModel}
            >
              {t("ceate_rightnow", "立即生成")}
            </Button>
          </Space>
        </Modal.Footer>
      </Form>
    </>
  );
};

export default ResponseGeneration;
