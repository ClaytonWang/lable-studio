import React, { useCallback, useEffect } from 'react';
import { Form, Tag } from 'antd';
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { Select } from '@/components/Form';
import { useAPI } from '@/providers/ApiProvider';
import { useProject } from '@/providers/ProjectProvider';

const formItemLayout = {
  labelCol: { span: 5 },
  wrapperCol: { span: 19 },
};

const IntentResponse = ({ close, execLabel, loading }) => {
  const { project } = useProject();
  const [execModel, setExecModel] = React.useState('');
  const [execModelList, setExecModelList] = React.useState([]);
  const api = useAPI();

  const projectLabels = project?.parsed_label_config?.intent?.labels ?? [];

  const getModelList = useCallback(async () => {
    const data = await api.callApi("modelList", {
      params: {
        project_id: project.id,
      },
    });

    setExecModelList([{ id:'',title:'请选择模型',version:'',value:'' },...data]);

  }, []);

  useEffect(() => {
    getModelList();
  }, []);

  const exec = () => {

    if (!execModel) {
      return;
    }

    //go exec
    execLabel({ model_id: execModel });
  };

  return (
    <>
      <Modal.Header>
        预标注(普通)
      </Modal.Header>
      <Form
        {...formItemLayout}
        layout="horizontal"
        name="form_in_modal"
        className='modal_form'
      >
        <Form.Item
          label="选择模型"
          validateStatus={execModel ? 'success' : 'error'}
          help={!execModel ? "请选择模型" : ''}
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
          label="项目标签"
        >
          <Space size="small">
            {
              projectLabels && projectLabels.map(tag => {
                return (
                  <Tag key={tag}>{tag}</Tag>
                );
              })
            }
          </Space>
        </Form.Item>
      </Form>
      <Modal.Footer>
        <Space align="end">
          <Button
            size="compact"
            onClick={close}
          >
            取消
          </Button>
          <Button
            size="compact"
            look="primary"
            onClick={exec}
            waiting={ loading }
            disabled={!execModel}
          >
            立即标注
          </Button>
        </Space>
      </Modal.Footer>
    </>
  );
};

export default IntentResponse;
