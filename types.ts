export type Construtora = 'MRV' | 'Direcional' | 'OlaCasaNova';
export type Carta = 'SBPE' | 'FGTS';

export interface Cliente {
  id: string;
  nome: string;
  cpf: string;
  sexo: 'Masculino' | 'Feminino';
  empreendimento: string;
  construtora: Construtora;
  carta: Carta;
  fichaCadastroPath?: string;
  criadoEm: string;
  atualizadoEm: string;
}

export interface MensagemTemplate {
  id: string;
  escopo: 'Global' | Construtora;
  carta?: Carta;
  titulo: string;
  gatilho?: string;
  corpo: string;
  autoDeleteAfterSend?: boolean;
  allowPostEdit?: boolean;
  ativo: boolean;
}

export interface Comando {
  id: string;
  trigger: string;
  preferirCartaEspecifica: boolean;
  modo: 'enviar-direto' | 'editar-apos-envio';
  obrigatorios?: string[];
}
